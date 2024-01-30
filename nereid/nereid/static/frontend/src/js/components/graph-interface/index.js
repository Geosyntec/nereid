import Editor from "./editor";
import { restoreSession } from "../session";

restoreSession();
export const editor = new Editor();
