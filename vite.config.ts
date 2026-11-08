import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({plugins:[react(),tailwindcss()],server:{proxy:{'/api':'http://127.0.0.1:8000'},fs:{deny:['.env','.env.*','*.{crt,pem}','**/.git/**','**/API.txt','**/api.txt','**/backend/**','**/.venv/**','**/output/**','**/*.log']},watch:{ignored:['**/*.md','**/docs/**','**/backend/**','**/output/**','**/.venv/**','**/*.log','**/tests/**','**/scripts/**','**/examples/**','**/API.txt']}},build:{rollupOptions:{output:{manualChunks:{charts:['recharts'],motion:['framer-motion'],markdown:['react-markdown','remark-gfm','remark-math','rehype-katex','rehype-highlight']}}}}});
