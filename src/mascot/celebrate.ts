export async function celebrate(){
 if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 const {default:confetti}=await import('canvas-confetti');
 confetti({particleCount:65,spread:65,startVelocity:28,origin:{y:.72},colors:['#20d9ef','#38a4ff','#b59cff','#ffd269'],disableForReducedMotion:true});
}
