/// <reference lib="webworker" />

declare const self: ServiceWorkerGlobalScope;

interface PushEvent extends ExtendableEvent {
  data: PushMessageData;
}

interface PushMessageData {
  json(): Promise<any>;
}

interface NotificationEvent extends ExtendableEvent {
  notification: Notification;
}

interface Notification {
  close(): void;
  data: {
    url: string;
  };
}

interface WindowClient {
  focused: boolean;
  focus(): Promise<WindowClient>;
}

interface Clients {
  matchAll(options: { type: string }): Promise<WindowClient[]>;
  openWindow(url: string): Promise<WindowClient>;
}

interface ServiceWorkerRegistration {
  active: ServiceWorker | null;
  showNotification(title: string, options: NotificationOptions): Promise<void>;
  unregister(): Promise<boolean>;
}

interface ServiceWorker extends EventTarget {
  dispatchEvent(event: Event): boolean;
} 