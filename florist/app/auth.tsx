import Cookies from "js-cookie";
import { createHash } from "crypto";

export function removeToken(): void {
    Cookies.remove("token");
}

export function setToken(token: string): void {
    Cookies.set("token", token, { expires: 7 });
}

export function getToken(): string | undefined {
    return Cookies.get("token");
}

export function isClient(): boolean {
    const componentType = typeof window === "undefined" ? "server" : "client";
    return componentType == "client";
}

export function getAuthHeaders(): [string, string][] {
    if (isClient()) {
        const token = getToken();
        if (token) {
            return [["Authorization", `Bearer ${token}`]];
        }
    }
    return [];
}

export function hashWord(word: string): string {
    return createHash("sha256").update(word).digest("hex");
}
