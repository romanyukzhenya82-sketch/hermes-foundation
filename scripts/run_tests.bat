@echo off
chcp 65001 >nul
echo ===============================================================================
echo 🧪 HERMES-FOUNDATION: Скрипт запуска интеграционных тестов
echo ===============================================================================
echo.

REM Переходим в корневую директорию проекта
cd /d "%~dp0"

echo 📂 Текущая директория: %CD%
echo.

REM Проверяем наличие Python
echo 🔍 Проверка установки Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Python не установлен!
    echo    Скачайте Python с https://www.python.org/downloads/
    echo    Убедитесь, что отметили "Add Python to PATH" при установке
    pause
    exit /b 1
)
python --version
echo ✅ Python найден
echo.

REM Проверяем наличие pip
echo 🔍 Проверка pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: pip не установлен!
    pause
    exit /b 1
)
echo ✅ pip найден
echo.

REM Устанавливаем зависимости
echo 📦 Установка зависимостей...
echo.
echo Устанавливаем ccxt (биржевой API)...
pip install ccxt -q
if %errorlevel% neq 0 (
    echo ⚠️  Ошибка установки ccxt, пробуем ещё раз...
    pip install ccxt
)

echo Устанавливаем pandas (обработка данных)...
pip install pandas -q
if %errorlevel% neq 0 (
    echo ⚠️  Ошибка установки pandas, пробуем ещё раз...
    pip install pandas
)

echo Устанавливаем numpy (численные вычисления)...
pip install numpy -q
if %errorlevel% neq 0 (
    echo ⚠️  Ошибка установки numpy, пробуем ещё раз...
    pip install numpy
)

echo Устанавливаем ta-lib (технический анализ)...
pip install ta-lib -q 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  ta-lib недоступен, установим pandas-ta вместо него...
    pip install pandas-ta -q
)

echo.
echo ✅ Все зависимости установлены!
echo.

REM Проверяем наличие тестового файла
echo 🔍 Проверка наличия тестового файла...
if not exist "tests\test_modules_integration.py" (
    echo ❌ ОШИБКА: Файл tests\test_modules_integration.py не найден!
    echo    Убедитесь, что вы запускаете скрипт из корневой папки проекта
    echo    Текущая директория: %CD%
    pause
    exit /b 1
)
echo ✅ Тестовый файл найден
echo.

REM Проверяем наличие модулей
echo 🔍 Проверка наличия модулей...
if not exist "src\analysis\market_regime.py" (
    echo ⚠️  ВНИМАНИЕ: Модуль market_regime.py не найден в src\analysis\
)
if not exist "src\analysis\volatility_analysis.py" (
    echo ⚠️  ВНИМАНИЕ: Модуль volatility_analysis.py не найден в src\analysis\
)
if not exist "src\analysis\risk_metrics.py" (
    echo ⚠️  ВНИМАНИЕ: Модуль risk_metrics.py не найден в src\analysis\
)
echo.

REM Запускаем тест
echo ===============================================================================
echo 🚀 ЗАПУСК ИНТЕГРАЦИОННОГО ТЕСТА
echo ===============================================================================
echo.
echo Тест будет:
echo   1. Загружать данные с Binance (BTC/USDT, 500 баров, 1h)
echo   2. Тестировать Market Regime Detection
echo   3. Тестировать Volatility Analysis
echo   4. Тестировать Risk Metrics
echo   5. Генерировать торговые рекомендации
echo.
echo ⏳ Пожалуйста, подождите...
echo.

REM Запускаем Python скрипт
python tests\test_modules_integration.py

REM Сохраняем код возврата
set TEST_RESULT=%errorlevel%

echo.
echo ===============================================================================
if %TEST_RESULT% equ 0 (
    echo ✅ ТЕСТ ЗАВЕРШЁН УСПЕШНО!
) else (
    echo ❌ ТЕСТ ЗАВЕРШЁН С ОШИБКАМИ ^(код: %TEST_RESULT%^)
)
echo ===============================================================================
echo.

REM Сохраняем результаты в файл
echo Сохранение результатов...
echo Тест выполнен: %date% %time% > test_results.log
echo Код возврата: %TEST_RESULT% >> test_results.log
echo ✅ Результаты сохранены в test_results.log
echo.

echo 📝 Для повторного запуска выполните: run_tests.bat
echo.
pause
exit /b %TEST_RESULT%
