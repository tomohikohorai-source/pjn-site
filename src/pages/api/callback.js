export const prerender = false;
export async function GET({ url }) {
  const code = url.searchParams.get('code');
  const clientID = process.env.GITHUB_CLIENT_ID;
  const clientSecret = process.env.GITHUB_CLIENT_SECRET;

  const res = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ client_id: clientID, client_secret: clientSecret, code })
  });

  const data = await res.json();
  const token = data.access_token;

  return new Response(`
    <script>
      const receiveMessage = (result) => {
        window.opener.postMessage("authorization:github:success:" + JSON.stringify({token: "${token}", provider: "github"}), window.location.origin);
        window.close();
      }
      receiveMessage();
    </script>
  `, { headers: { 'Content-Type': 'text/html' } });
}
