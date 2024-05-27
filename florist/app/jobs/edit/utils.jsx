export async function postJob(body) {
    return await fetch("/api/server/job", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body,
    });
}
