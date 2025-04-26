const puppeteer = require('puppeteer');

async function solveCaptcha() {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto('http://example.com/captcha', { waitUntil: 'networkidle2' });
    const captchaImage = await page.$('img.captcha');
    if (captchaImage) {
        const screenshot = await captchaImage.screenshot({ encoding: 'base64' });
        await page.type('#captchaInput', 'solved_text');
        await page.click('#submitCaptcha');
        const result = await page.waitForSelector('#captchaResult', { timeout: 5000 })
            .then(() => 'Éxito')
            .catch(() => 'Fallo');
        await browser.close();
        return { image: screenshot, result: result };
    }
    await browser.close();
    return { image: null, result: 'No se encontró CAPTCHA' };
}

solveCaptcha().then(result => {
    console.log(JSON.stringify(result));
}).catch(err => {
    console.error(JSON.stringify({ image: null, result: 'Error: ' + err.message }));
});