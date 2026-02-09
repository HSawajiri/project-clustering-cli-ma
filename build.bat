@echo off
chcp 65001 >nul
REM PyInstaller ビルドスクリプト (Windows)
REM Project Clustering CLI MA

echo ============================================================
echo プロジェクト名クラスタリングツール ビルド開始
echo ============================================================
echo.

REM 依存関係インストール
echo [1/3] 依存関係をインストール中...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo エラー: 依存関係のインストールに失敗しました
    pause
    exit /b 1
)
echo 完了: 依存関係のインストールが完了しました
echo.

REM PyInstallerインストール
echo [2/3] PyInstallerをインストール中...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo エラー: PyInstallerのインストールに失敗しました
    pause
    exit /b 1
)
echo 完了: PyInstallerのインストールが完了しました
echo.

REM ビルド実行
echo [3/3] PyInstallerでビルド中...
pyinstaller build.spec
if %errorlevel% neq 0 (
    echo エラー: ビルドに失敗しました
    pause
    exit /b 1
)
echo 完了: ビルドが完了しました
echo.

REM 完了メッセージ
echo ============================================================
echo ビルド完了
echo ============================================================
echo 実行ファイル: dist\clustering.exe
echo.
echo 配布方法:
echo   1. dist\clustering.exe を配布フォルダにコピー
echo   2. config.yaml を同じフォルダにコピー
echo   3. 入力CSVファイルを同じフォルダに配置
echo   4. clustering.exe を実行
echo.
echo 使用例:
echo   clustering.exe
echo   clustering.exe --input data.csv
echo   clustering.exe --config custom_config.yaml
echo.
pause
