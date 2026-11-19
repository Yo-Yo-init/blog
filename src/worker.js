// Cloudflare Worker entry for the blog.
//
// Everything is served from the static assets in ./dist. The one thing this
// script adds: requests that arrive on the OLD hostname are sent to the new
// domain with a permanent (301) redirect, keeping the path and query string,
// so old links and search results follow the move.
//
// Remove OLD_HOSTS entries (and the old route in wrangler.jsonc) when the
// old domain is finally retired; once the list is empty this is a pure
// pass-through.

const NEW_ORIGIN = "https://chililab.dev";
const OLD_HOSTS = new Set(["pepperslab.habanada.com"]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (OLD_HOSTS.has(url.hostname)) {
      return Response.redirect(NEW_ORIGIN + url.pathname + url.search, 301);
    }
    return env.ASSETS.fetch(request);
  },
};
