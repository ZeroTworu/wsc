
export const EventType = {
    MESSAGE: "MESSAGE",
    USER_JOIN_CHAT: "USER_JOIN_CHAT",
    USER_LEFT_CHAT: "USER_LEFT_CHAT",
    PING: "PING",
    PONG: "PONG",
} as const;

export type BusEventType = typeof EventType[keyof typeof EventType];
