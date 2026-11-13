import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { isIP } from 'node:net';

const lanHosts=(process.env.LUMINA_LAN_HOSTS||'').split(',').map(host=>host.trim()).filter(host=>isIP(host)===4&&/^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)/.test(host));
const frontendOrigins=['http://localhost:5173','http://127.0.0.1:5173',...lanHosts.map(host=>`http://${host}:5173`)];

export default defineConfig({
 plugins:[react(),tailwindcss()],
 server:{
  cors:{origin:frontendOrigins,methods:['GET','HEAD','POST','PUT','DELETE','OPTIONS'],allowedHeaders:['Content-Type']},
  proxy:{'/api':{target:'http://127.0.0.1:8000',changeOrigin:true}},
  fs:{deny:['.env','.env.*','*.{crt,pem}','**/.git/**','**/API.txt','**/api.txt','**/backend/**','**/.venv/**','**/output/**','**/*.log']},
  watch:{ignored:['**/*.md','**/docs/**','**/backend/**','**/output/**','**/.venv/**','**/*.log','**/tests/**','**/scripts/**','**/examples/**','**/API.txt']}
 },
 build:{rollupOptions:{output:{manualChunks:{charts:['recharts'],motion:['framer-motion'],markdown:['react-markdown','remark-gfm','remark-math','rehype-katex','rehype-highlight']}}}}
});
