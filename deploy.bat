@echo off
echo Deploying PingGov to Vercel...
echo.

REM Set Node.js path
set PATH=%PATH%;C:\Program Files\nodejs

REM Install and run Vercel
echo Installing Vercel CLI...
npm install -g vercel

echo.
echo Starting deployment...
vercel --prod

echo.
echo Deployment complete!
pause
