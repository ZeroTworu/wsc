import mitt from "mitt";

export type BusEventType = {
  MESSAGE: string;
}



export const eventBus = mitt<BusEventType>();
