"use client";

import { MessagesTable } from "@/components/messages/MessagesTable";

export default function MessagesPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Messages</h2>
      <MessagesTable />
    </div>
  );
}
