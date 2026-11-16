import postgres from 'postgres';
import { env } from '$env/dynamic/private';

let client: ReturnType<typeof postgres> | null = null;

// Lazy so that `vite build` works without a database; a missing DATABASE_URL
// fails on the first query instead of silently using a default password.
function db() {
	if (!client) {
		if (!env.DATABASE_URL) throw new Error('DATABASE_URL není nastavené');
		// Brain uses the SQLAlchemy URL (postgresql+psycopg://...), postgres.js wants postgres://
		client = postgres(env.DATABASE_URL.replace(/^postgresql\+psycopg:/, 'postgresql:'), { max: 5 });
	}
	return client;
}

export const sql = new Proxy((() => {}) as unknown as ReturnType<typeof postgres>, {
	apply: (_t, _this, args) => (db() as unknown as (...a: unknown[]) => unknown)(...args),
	get: (_t, prop) => Reflect.get(db(), prop)
});
