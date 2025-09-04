import request from "@/utils/request";

export const loginApi = (data) => request.post("/login", data);

export const resetApi = (data) => request.put("/reset", data);
