import postgres from 'postgres';
import { env } from '$env/dynamic/private';

// Brain používá SQLAlchemy URL (postgresql+psycopg://...), postgres.js chce čisté postgres://
const url = (env.DATABASE_URL ?? 'postgresql://chatshop:chatshop@localhost:5432/chatshop').replace(
	/^postgresql\+psycopg:/,
	'postgresql:'
);

export const sql = postgres(url, { max: 5 });
