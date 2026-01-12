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

    // トークンを親ウィンドウに渡し、確実にウィンドウを閉じる命令
    const responseHtml = `
      <!DOCTYPE html>
      <html>
      <body>
        <script>
          (function() {
            const token = "${token}";
            const message = "authorization:github:success:" + JSON.stringify({
              token: token,
              provider: "github"
            });
            
            // 親ウィンドウ（管理画面）にトークンを送信
            window.opener.postMessage(message, window.location.origin);
            
            // 少し待ってから閉じる（確実に送信するため）
            setTimeout(() => {
              window.close();
            }, 500);
          })();
        </script>
        認証に成功しました。この画面は自動的に閉じます。
      </body>
      </html>
    `;

    return new Response(responseHtml, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  } catch (e) {
    return new Response("エラーが発生しました: " + e.message, { status: 500 });
  }
}
