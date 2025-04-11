import mitt from "mitt";

export type BusEventType = {
  MESSAGE: string;
  UPDATE_READERS: string;
}



export const eventBus = mitt<BusEventType>();
