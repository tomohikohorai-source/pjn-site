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

    // トークンが空でないか確認
    if (!token) {
      return new Response("GitHubトークンの取得に失敗しました。ClientID/Secretが正しいか確認してください。", { status: 500 });
    }

    // 文字化けを防ぐため UTF-8 を指定したレスポンス
    const html = `
      <!DOCTYPE html>
      <html lang="ja">
      <head><meta charset="utf-8"></head>
      <body>
        <p>認証に成功しました。管理画面に移動します...</p>
        <script>
          (function() {
            const message = "authorization:github:success:" + JSON.stringify({
              token: "${token}",
              provider: "github"
            });
            // 管理画面（親ウィンドウ）へメッセージを送信
            window.opener.postMessage(message, window.location.origin);
            // 0.5秒後に自動で閉じる
            setTimeout(() => window.close(), 500);
          })();
        </script>
      </body>
      </html>
    `;

    return new Response(html, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  } catch (e) {
    return new Response("接続エラーが発生しました: " + e.message, { status: 500 });
  }
}
