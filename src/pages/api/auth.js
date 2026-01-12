export const prerender = false;
export async function GET({ redirect }) {
  const clientID = process.env.GITHUB_CLIENT_ID;
  const url = `https://github.com/login/oauth/authorize?client_id=${clientID}&scope=repo,user`;
  return redirect(url);
}
