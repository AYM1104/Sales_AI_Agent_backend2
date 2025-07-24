from fastapi import FastAPI
import os


app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI is alive!"}


print(f"PORT: {os.environ.get('PORT')}")


# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.config import settings
# from app.api.routes import router
# # from app.api.pdf_routes import router as pdf_router

# def create_app() -> FastAPI:
#     """FastAPIアプリケーションを作成"""
#     app = FastAPI(
#         title="顧客理解AIエージェント API",
#         description="企業分析とソリューション提案API",
#         version="1.0.0"
#     )

#     # CORS設定
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=settings.ALLOWED_ORIGINS,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

#     @app.get("/")
#     def root():
#         return {"message": "App is running"}

#     # ★ここに追加 - 起動時イベント
#     @app.on_event("startup")
#     async def startup_event():
#         print("=== 環境変数確認 ===")
        
#         # 全ての環境変数を確認
#         import os
#         all_vars = dict(os.environ)
#         print(f"全環境変数数: {len(all_vars)}")
        
#         # Google関連の変数を探す
#         google_vars = {k: v for k, v in all_vars.items() if 'GOOGLE' in k.upper()}
#         print(f"Google関連変数: {google_vars}")
        
#         # 具体的に確認
#         api_key = os.getenv('GOOGLE_API_KEY')
#         print(f"GOOGLE_API_KEY: {api_key is not None}")
#         if api_key:
#             print(f"キーの長さ: {len(api_key)}")
#             print(f"最初の10文字: {api_key[:10]}...")
        
#         print("================")

#     # ルーターを登録
#     app.include_router(router)
#     # app.include_router(pdf_router)

#     return app

# app = create_app()



# # import os
# # from fastapi import FastAPI
# # from google.generativeai import GenerativeModel
# # import google.generativeai as genai
# # from dotenv import load_dotenv

# # from app.config import Settings
# # from app.api.routes import router

# # load_dotenv()


# # app = FastAPI(title="Gemini Test API")

# # # Gemini設定
# # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# # if not GOOGLE_API_KEY:
# #     raise ValueError("GOOGLE_API_KEY not found")

# # genai.configure(api_key=GOOGLE_API_KEY)
# # model = GenerativeModel("gemini-2.5-pro")

# # @app.get("/")
# # async def root():
# #     return {"message": "Gemini Test API"}

# # @app.get("/test")
# # async def test_gemini():
# #     try:
# #         response = model.generate_content("Hello, how are you?")
# #         return {
# #             "success": True,
# #             "response": response.text
# #         }
# #     except Exception as e:
# #         return {
# #             "success": False,
# #             "error": str(e)
# #         }

# # @app.post("/analyze")
# # async def analyze_company(company_name: str):
# #     try:
# #         prompt = f"{company_name}について100文字程度で説明してください。"
# #         response = model.generate_content(prompt)
# #         return {
# #             "success": True,
# #             "company": company_name,
# #             "analysis": response.text
# #         }
# #     except Exception as e:
# #         return {
# #             "success": False,
# #             "error": str(e)
# #         }

# # @app.post("/full-analysis")
# # async def full_analysis(company_name: str):
# #     """長いプロンプトでの企業分析テスト"""
# #     try:
# #         print(f"=== 完全プロンプトテスト開始: {company_name} ===")
        
# #         # あなたの長いプロンプト
# #         full_prompt = """あなたは企業の有価証券報告書を分析し、IoTソリューション提案営業の観点から重要な情報を整理する専門家です。
# # 以下の企業を分析し、営業戦略立案に役立つ情報を抽出してください。
# # 対象企業：[企業名を入力]
# # 分析観点と出力形式
# # 1. 事業概況とIoT親和性
# # 主力事業領域：製造業、物流、小売、インフラなど
# # 事業規模と成長性：売上高推移、利益率、成長戦略
# # IoT導入可能性の高い事業領域：具体的にどの事業部門でIoTが活用できそうか
# # デジタル化への取り組み状況：DX推進、IT投資の記載があるか
# # 2. 経営課題と痛み
# # 業績上の課題：コスト増、効率性の問題、競争力低下など
# # 事業リスク：報告書に記載されているリスク要因
# # 人手不足・労働力問題：人員配置、採用難、高齢化等の課題
# # 品質・安全管理：品質向上、事故防止、コンプライアンス強化のニーズ
# # 3. 財務状況と投資余力
# # 財務健全性：自己資本比率、現金保有額、借入状況
# # 設備投資動向：過去3年の設備投資額と投資方針
# # IT・デジタル投資：システム関連投資の記載
# # 投資回収への姿勢：ROI重視か、長期投資志向か
# # 4. 組織体制と意思決定
# # 経営陣の背景：技術系出身者、変革志向の経営者がいるか
# # 組織構造：事業部制、機能別組織など、意思決定プロセスの推測
# # 子会社・関連会社：グループ全体でのIoT導入可能性
# # 地理的展開：国内外の事業所、工場の分散状況
# # 5. 競合環境と差別化ニーズ
# # 競争環境：業界内でのポジション、競合他社との差別化課題
# # 技術革新への対応：新技術導入、イノベーション創出の取り組み
# # 顧客からの要求：品質向上、納期短縮、コスト削減等の圧力
# # 6. 提案機会の特定
# # 短期的提案テーマ：すぐに提案できそうな課題解決領域
# # 中長期的提案テーマ：将来的な事業変革に関わる大型案件の可能性
# # アプローチすべき部門：製造部門、物流部門、IT部門など
# # 提案時の訴求ポイント：コスト削減、品質向上、効率化、新規事業創出
# # 出力フォーマット
# # 各項目について、具体的な根拠（有価証券報告書のページ数や記載内容の引用）とともに整理してください。情報が不足している場合は「記載なし」と明記し、推測で補完する場合は「推測」と明示してください。
# # 補足指示
# # 数値データは具体的に記載（売上高○億円、従業員数○人など）
# # 業界特有の課題やトレンドも考慮して分析
# # 競合他社の動向も踏まえた相対的な位置づけを意識
# # 提案の優先順位付けも含めて整理"""

# #         # 企業名を置換
# #         final_prompt = full_prompt.replace("[企業名を入力]", company_name)
# #         print(f"プロンプト長: {len(final_prompt)} 文字")
        
# #         # Gemini API呼び出し
# #         response = model.generate_content(final_prompt)
# #         print("完全プロンプト成功！")
        
# #         return {
# #             "success": True,
# #             "company": company_name,
# #             "prompt_length": len(final_prompt),
# #             "analysis": response.text
# #         }
        
# #     except Exception as e:
# #         print(f"完全プロンプトエラー: {e}")
# #         return {
# #             "success": False,
# #             "company": company_name,
# #             "error": str(e)
# #         }
    
# # # ルーターを登録
# #     app.include_router(router)

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8000)