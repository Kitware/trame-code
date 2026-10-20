// utils/ and themes/ are shared verbatim with vue-components and ship no types
declare module "@shared/utils/monacoEnv";
declare module "@shared/utils/textmate";

// provided by the trame react client
interface Window {
  trame?: any;
}
