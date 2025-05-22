
export const EventType = {
    MESSAGE: "MESSAGE",
    USER_JOIN_CHAT: "USER_JOIN_CHAT",
    USER_LEFT_CHAT: "USER_LEFT_CHAT",
    USER_ENTER_CHAT: "USER_ENTER_CHAT",
    USER_EXIT_CHAT: "USER_EXIT_CHAT",
    PING: "PING",
    PONG: "PONG",
    UPDATE_READERS: "UPDATE_READERS",
} as const;

export type BusEventType = typeof EventType[keyof typeof EventType];
