
export const EventType = {
    Message: "MESSAGE",
    UserJoin: "USER_JOIN",
    UserLeft: "USER_LEFT",
    Ping: "PING",
} as const;

export type BusEventType = typeof EventType[keyof typeof EventType];
