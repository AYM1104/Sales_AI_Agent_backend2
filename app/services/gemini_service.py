import os
import yaml
import fitz  # PyMuPDF
import requests
from typing import List, Dict, Any
from google.generativeai import GenerativeModel
import google.generativeai as genai
from app.config import settings
from app.models.schemas import Solution

class GeminiService:
    """Gemini API サービス"""
    
    def __init__(self):
        print(f"=== GeminiService初期化開始 ===")
        print(f"GOOGLE_API_KEY存在: {bool(settings.GOOGLE_API_KEY)}")
        print(f"GEMINI_MODEL_NAME: {settings.GEMINI_MODEL_NAME}")
        
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY が設定されていません")
        
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            print("genai.configure 成功")
            
            self.model = GenerativeModel(model_name=settings.GEMINI_MODEL_NAME)
            print("GenerativeModel 作成成功")
            
        except Exception as e:
            print(f"GeminiService初期化エラー: {e}")
            print(f"エラータイプ: {type(e)}")
            raise
        
        print("=== GeminiService初期化完了 ===")
    
    def _load_yaml_prompt(self, filename: str) -> Dict[str, Any]:
        """YAMLプロンプトファイルを読み込み"""
        filepath = os.path.join(settings.PROMPTS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def _load_prompt(self, filename: str) -> str:
        """プロンプトファイルを読み込み"""
        filepath = os.path.join(settings.PROMPTS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    
    def _build_prompt_from_yaml(self, yaml_data: Dict[str, Any], step_name: str, **kwargs) -> str:
        """YAMLデータからプロンプトを構築"""
        prompt_parts = []
        
        # commonセクションの処理
        if "common" in yaml_data:
            common = yaml_data["common"]
            
            # intro（導入部分）
            if "intro" in common:
                intro = common["intro"]
                # 変数の置換
                for key, value in kwargs.items():
                    intro = intro.replace(f"{{{key}}}", str(value))
                prompt_parts.append(intro)
            
            # instructions（指示）
            if "instructions" in common:
                instructions = common["instructions"]
                # 変数の置換
                for key, value in kwargs.items():
                    instructions = instructions.replace(f"{{{key}}}", str(value))
                prompt_parts.append(instructions)
        
        # ステップ固有の内容
        if step_name in yaml_data:
            step_content = yaml_data[step_name]
            # 変数の置換
            for key, value in kwargs.items():
                step_content = step_content.replace(f"{{{key}}}", str(value))
            prompt_parts.append(step_content)
        
        return "\n\n".join(prompt_parts)
   
    async def summarize_securities_report(self, pdf_url: str, company_name: str) -> str:
        """有価証券報告書を要約"""
        try:
            print(f"=== summarize_securities_report 開始 ===")
            print(f"PDF URL: {pdf_url}")
            print(f"企業名: {company_name}")
            
            # 1. PDFデータをダウンロード
            print("PDFダウンロード開始...")
            response = requests.get(pdf_url)
            response.raise_for_status()
            print(f"PDFダウンロード成功: {len(response.content)} bytes")
            
            # 2. fitz で PDF を読み込む
            print("PDF読み込み開始...")
            doc = fitz.open(stream=response.content, filetype="pdf")
            print(f"PDF読み込み成功: {len(doc)} pages")
            
            # 3. テキスト抽出
            print("テキスト抽出開始...")
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            print(f"テキスト抽出成功: {len(full_text)} 文字")


            # 4. 段階的要約実行
            print("段階的要約開始...")
            
            # YAML設定ファイル名とステップ名のリスト（順序重要）
            yaml_steps = [
                ("company_analysis_prompts/company_analysis_step1.yml", "step1"),
                ("company_analysis_prompts/company_analysis_step2.yml", "step2"), 
                ("company_analysis_prompts/company_analysis_step3.yml", "step3"),
                ("company_analysis_prompts/company_analysis_step4.yml", "step4"),
                ("company_analysis_prompts/company_analysis_step5.yml", "step5"),
                ("company_analysis_prompts/company_analysis_step6.yml", "step6")
            ]
            
            current_text = full_text[:settings.MAX_PDF_CHARS]
            step_results = {}
            
            for i, (yaml_file, step_name) in enumerate(yaml_steps, 1):
                print(f"--- ステップ {i}: {yaml_file} ({step_name}) 実行開始 ---")
                
                try:
                    # YAMLファイル読み込み
                    yaml_data = self._load_yaml_prompt(yaml_file)
                    print(f"YAML読み込み成功: {yaml_file}")
                    
                    # プロンプト構築
                    prompt = self._build_prompt_from_yaml(
                        yaml_data,
                        step_name,
                        company_name=company_name,
                        securities_report=current_text,
                        previous_results=step_results
                    )
                    
                    # プロンプトにデータを追加
                    if i == 1:
                        # 最初のステップでは元のテキストを使用
                        final_prompt = prompt + "\n\n## 分析対象の有価証券報告書\n" + current_text
                    else:
                        # 2ステップ目以降は前のステップの結果も含める
                        context = "\n".join([f"### ステップ{j}の結果\n{result}" 
                                           for j, result in step_results.items()])
                        final_prompt = prompt + "\n\n## 前のステップの分析結果\n" + context + "\n\n## 元の有価証券報告書（参考）\n" + current_text[:10000]
                    
                    print(f"最終プロンプト準備完了: {len(final_prompt)} 文字")
                    
                    # Gemini API呼び出し
                    print(f"Gemini API呼び出し開始（ステップ{i}）...")
                    response = self.model.generate_content(final_prompt)
                    
                    if not response.text:
                        raise Exception(f"ステップ{i}でレスポンスが空でした")
                    
                    step_results[i] = response.text
                    print(f"ステップ{i}完了: {len(response.text)} 文字")
                    
                    # 次のステップのために結果を現在のテキストとして設定
                    if i < len(yaml_steps):
                        current_text = response.text
                    
                except Exception as e:
                    print(f"ステップ{i}でエラー: {e}")
                    print(f"エラータイプ: {type(e)}")
                    raise Exception(f"ステップ{i}（{yaml_file}）の処理中にエラーが発生しました: {e}")
            
            print("=== 段階的要約完了 ===")

            # 最終結果を返す（最後のステップの結果）
            final_result = step_results[len(yaml_steps)]
            print(f"最終結果: {len(final_result)} 文字")
            
            return final_result











            
            # # 4. プロンプトファイルを読み込む
            # print("プロンプト読み込み開始...")
            # prompt_template = self._load_prompt("prompt.txt")
            # print(f"プロンプトテンプレート読み込み成功: {len(prompt_template)} 文字")
            
            # prompt_text = prompt_template.replace("[企業名を入力]", company_name) + "\n" + text[:settings.MAX_PDF_CHARS]
            # print(f"最終プロンプト準備完了: {len(prompt_text)} 文字")
            # print(f"MAX_PDF_CHARS設定: {settings.MAX_PDF_CHARS}")
            
            # # 5. Gemini APIで要約を取得
            # print("Gemini API呼び出し開始...")
            # print(f"使用モデル: {settings.GEMINI_MODEL_NAME}")
            
            # response = self.model.generate_content(prompt_text)
            # print("Gemini API呼び出し成功")
            # print(f"レスポンス取得: {len(response.text) if response.text else 0} 文字")
            
            # return response.text
            
        except requests.RequestException as e:
            print(f"PDFダウンロードエラー: {e}")
            raise
        except Exception as e:
            print(f"summarize_securities_report エラー: {e}")
            print(f"エラータイプ: {type(e)}")
            import traceback
            print(f"スタックトレース: {traceback.format_exc()}")
            raise
        
    async def generate_hypothesis(
        self, 
        summary: str, 
        department_name: str, 
        position_name: str, 
        job_scope: str
    ) -> str:
        """仮説を生成"""
        try:
            print(f"=== generate_hypothesis 開始 ===")
            print(f"部署名: {department_name}")
            print(f"役職: {position_name}")
            print(f"業務範囲: {job_scope}")
            
            # YAMLファイル読み込み
            yaml_data = self._load_yaml_prompt("hypothesis_prompt.yml")
            print(f"hypothesis_prompt.yml 読み込み成功")
            
            # プロンプトテンプレート取得
            prompt_template = yaml_data["hypothesis_prompt"]["template"]
            
            # 変数置換
            prompt = prompt_template.replace("{securities_report_summary}", summary)
            prompt = prompt.replace("{department_name}", department_name)
            prompt = prompt.replace("{position_name}", position_name)
            prompt = prompt.replace("{job_scope}", job_scope)

            print(f"最終プロンプト準備完了: {len(prompt)} 文字")
            
            # Gemini API呼び出し
            print("Gemini API呼び出し開始（仮説生成）...")
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise Exception("仮説生成でレスポンスが空でした")
            
            hypothesis_text = response.text
            
            print(f"仮説生成完了: {len(hypothesis_text)} 文字")
            return hypothesis_text
        
        except Exception as e:
            print(f"generate_hypothesis エラー: {e}")
            print(f"エラータイプ: {type(e)}")
            import traceback
            print(f"スタックトレース: {traceback.format_exc()}")
            raise




        # """仮説を生成"""
        # prompt_template = self._load_prompt("hypothesis_prompt.txt")
        # prompt = prompt_template.replace("{securities_report_summary}", summary)
        # prompt = prompt.replace("{department_name}", department_name)
        # prompt = prompt.replace("{position_title}", position_name)
        # prompt = prompt.replace("{job_scope}", job_scope)
        
        # response = self.model.generate_content(prompt)
        # return response.text
    
    async def match_solutions(self, hypothesis: str, solutions: List[Solution]) -> str:
        """ソリューションマッチング"""
        try:
            print(f"=== match_solutions 開始 ===")
            print(f"ソリューション数: {len(solutions)}")
            
            # YAMLファイル読み込み
            yaml_data = self._load_yaml_prompt("solution_matching_prompt.yml")
            print(f"solution_matching_prompt.yml 読み込み成功")
            
            # プロンプトテンプレート取得
            if "matching_prompt" not in yaml_data or "template" not in yaml_data["matching_prompt"]:
                raise Exception("solution_matching_prompt.yml の構造が正しくありません")
            
            prompt_template = yaml_data["matching_prompt"]["template"]
            
            # ソリューション情報をテキスト化
            solutions_text = "\n".join([
                f"・{s.name}：{s.features}（用途：{s.use_case}）"
                for s in solutions
            ])
            
            # 変数置換
            prompt = prompt_template.replace("{hypothesis}", hypothesis)
            prompt = prompt.replace("{solutions}", solutions_text)
            
            print(f"[ソリューションマッチング] プロンプト文字数: {len(prompt)} 文字")
            
            # Gemini API呼び出し
            print("Gemini API呼び出し開始（ソリューションマッチング）...")
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise Exception("ソリューションマッチングでレスポンスが空でした")
            
            print(f"[ソリューションマッチング] Gemini応答文字数: {len(response.text)} 文字")
            return response.text
            
        except Exception as e:
            print(f"match_solutions エラー: {e}")
            print(f"エラータイプ: {type(e)}")
            import traceback
            print(f"スタックトレース: {traceback.format_exc()}")
            raise
    
    async def generate_hearing_items(
        self,
        company_name: str,
        department_name: str,
        position_name: str,
        hypothesis_text: str
    ) -> str:
        """ヒアリング項目を生成"""
        try:
            print(f"=== generate_hearing_items 開始 ===")
            print(f"企業名: {company_name}")
            print(f"部署名: {department_name}")
            print(f"役職: {position_name}")
            
            # YAMLファイル読み込み
            yaml_data = self._load_yaml_prompt("hearing_prompt.yml")
            print(f"hearing_prompt.yml 読み込み成功")
            
            # プロンプトテンプレート取得
            if "hearing_prompt" not in yaml_data or "template" not in yaml_data["hearing_prompt"]:
                raise Exception("hearing_prompt.yml の構造が正しくありません")
            
            prompt_template = yaml_data["hearing_prompt"]["template"]
            
            # 変数置換
            prompt = prompt_template.replace("{company_name}", company_name)
            prompt = prompt.replace("{department_name}", department_name)
            prompt = prompt.replace("{position_name}", position_name)
            prompt = prompt.replace("{company_size}", "※有価証券報告書をもとに推定してください")
            prompt = prompt.replace("{industry}", "※報告書から業界を判断してください")
            prompt = prompt.replace("{hypothesis}", hypothesis_text)
            
            print(f"[ヒアリング生成] プロンプト文字数: {len(prompt)} 文字")
            
            # Gemini API呼び出し
            print("Gemini API呼び出し開始（ヒアリング項目生成）...")
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise Exception("ヒアリング項目生成でレスポンスが空でした")
            
            print(f"[ヒアリング生成] Gemini応答文字数: {len(response.text)} 文字")
            return response.text
            
        except Exception as e:
            print(f"generate_hearing_items エラー: {e}")
            print(f"エラータイプ: {type(e)}")
            import traceback
            print(f"スタックトレース: {traceback.format_exc()}")
            raise