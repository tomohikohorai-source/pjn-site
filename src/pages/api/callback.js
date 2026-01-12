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

    if (!token) {
      return new Response("トークンの取得に失敗しました。VercelのEnvironment Variablesを確認してください。", { status: 500 });
    }

    // 文字化けを防ぎ、確実に親画面へメッセージを送り、確実に閉じるHTML
    const html = `
      <!DOCTYPE html>
      <html lang="ja">
      <head>
        <meta charset="utf-8">
        <title>認証完了</title>
      </head>
      <body>
        <div id="status">認証に成功しました。まもなく管理画面に戻ります...</div>
        <script>
          (function() {
            const token = "${token}";
            const message = "authorization:github:success:" + JSON.stringify({
              token: token,
              provider: "github"
            });
            
            // 全ての可能性を考慮してメッセージを送信
            if (window.opener) {
              // ターゲットを "*" にすることで、オリジンの不一致によるブロックを回避
              window.opener.postMessage(message, "*");
              console.log("Success: Token sent to opener.");
            } else {
              document.getElementById("status").innerText = "エラー：親ウィンドウが見つかりません。";
            }
            
            // 確実に送信を完了させるために1秒待ってから閉じる
            setTimeout(() => {
              window.close();
            }, 1000);
          })();
        </script>
      </body>
      </html>
    `;

    return new Response(html, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  } catch (e) {
    return new Response("接続エラー: " + e.message, { status: 500 });
  }
}
