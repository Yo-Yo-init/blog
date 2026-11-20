// Cloudflare Worker entry for the blog.
//
// Everything is served from the static assets in ./dist. This script adds two
// permanent (301) redirects, both keeping the rest of the URL where it makes sense:
//
//  1. The OLD hostname goes to the new domain (path and query kept).
//  2. Legacy filter links on the blog index go to their real pages:
//       /blog/?q=<tag-slug>        ->  /blog/tag/<tag-slug>/
//       /blog/?category=<slug>     ->  /blog/category/<slug>/
//     Only when that page exists (checked against the static assets), so free-text
//     queries and unknown values fall through to the normal /blog/ page.
//
// Remove OLD_HOSTS entries (and the old route in wrangler.jsonc) when the old domain
// is finally retired.

const NEW_ORIGIN = "https://chililab.dev";
const OLD_HOSTS = new Set(["pepperslab.habanada.com"]);
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

async function legacyFilterTarget(url, env) {
  if (url.pathname !== "/blog" && url.pathname !== "/blog/") return null;
  const params = url.searchParams;
  const keys = [...params.keys()];
  if (keys.length !== 1 || !["q", "category"].includes(keys[0])) return null;
  const value = (params.get(keys[0]) || "").trim().toLowerCase();
  if (!SLUG.test(value)) return null;
  const path = keys[0] === "q" ? `/blog/tag/${value}/` : `/blog/category/${value}/`;
  const probe = await env.ASSETS.fetch(new Request(new URL(path, url.origin), { method: "HEAD" }));
  return probe.status === 200 ? path : null;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (OLD_HOSTS.has(url.hostname)) {
      return Response.redirect(NEW_ORIGIN + url.pathname + url.search, 301);
    }
    const target = await legacyFilterTarget(url, env);
    if (target) {
      return Response.redirect(new URL(target, url.origin).toString(), 301);
    }
    return env.ASSETS.fetch(request);
  },
};
