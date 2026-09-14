import { next } from "@vercel/functions";

function unauthorized() {
  return new Response("Acesso protegido. Informe as credenciais do site.", {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="PC Monitor", charset="UTF-8"',
      "Cache-Control": "no-store",
      "Content-Type": "text/plain; charset=utf-8",
    },
  });
}

function safeEqual(left, right) {
  if (left.length !== right.length) return false;
  let result = 0;
  for (let index = 0; index < left.length; index += 1) {
    result |= left.charCodeAt(index) ^ right.charCodeAt(index);
  }
  return result === 0;
}

export default function middleware(request) {
  const configuredPassword = process.env.SITE_PASSWORD;
  const configuredUser = process.env.SITE_USERNAME || "pc-monitor";

  // Fail closed: a deployment without the secret never publishes the site.
  if (!configuredPassword) return unauthorized();

  const authorization = request.headers.get("authorization") || "";
  if (!authorization.startsWith("Basic ")) return unauthorized();

  try {
    const decoded = atob(authorization.slice(6));
    const separator = decoded.indexOf(":");
    if (separator < 0) return unauthorized();

    const username = decoded.slice(0, separator);
    const password = decoded.slice(separator + 1);
    if (!safeEqual(username, configuredUser) || !safeEqual(password, configuredPassword)) {
      return unauthorized();
    }
  } catch {
    return unauthorized();
  }

  return next({
    headers: {
      "Cache-Control": "private, no-store",
    },
  });
}
