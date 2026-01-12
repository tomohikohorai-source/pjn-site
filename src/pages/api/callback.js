export const prerender = false;
export async function GET({ url }) {
  const code = url.searchParams.get('code');
  const clientID = process.env.GITHUB_CLIENT_ID;
  const clientSecret = process.env.GITHUB_CLIENT_SECRET;

  try {
    const res = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ client_id: clientID, client_secret: clientSecret, code })
    });
    const data = await res.json();
    const token = data.access_token;

    // トークンをブラウザの保存領域（LocalStorage）に強制的に書き込みます
    const html = `
      <!DOCTYPE html>
      <html>
      <head><meta charset="utf-8"></head>
      <body>
        <p>認証に成功しました。このウィンドウを閉じ、元の画面を再読み込み（リフレッシュ）してください。</p>
        <script>
          const token = "${token}";
          const userStr = JSON.stringify({ token: token, provider: "github" });
          
          // 親ウィンドウへの送信と、自身の保存の両方を行います
          if (window.opener) {
            window.opener.postMessage("authorization:github:success:" + userStr, "*");
          }
          localStorage.setItem('decap-cms-user', userStr);
          
          // 2秒後に自動で閉じます
          setTimeout(() => { window.close(); }, 2000);
        </script>
      </body>
      </html>
    `;
    return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
  } catch (e) {
    return new Response(e.message, { status: 500 });
  }
}
