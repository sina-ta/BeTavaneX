"use client";

import { useState } from "react";
import { use } from "react";

export default function WorkUnitDetail({
  params,
}: {
  params: Promise<{ unitId: string }>;
}) {
  const resolvedParams = use(params);

  const [quantity, setQuantity] = useState("");
  const [notes, setNotes] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    console.log({
      unitId: resolvedParams.unitId,
      quantity,
      notes,
      date: new Date(),
    });

    setQuantity("");
    setNotes("");
  };

  return (
    <div className="max-w-xl space-y-6">
      <h1 className="text-2xl font-bold">
        Daily Log — Unit {resolvedParams.unitId}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="number"
          placeholder="Quantity Completed Today"
          className="w-full border p-2 rounded"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />

        <textarea
          placeholder="Notes"
          className="w-full border p-2 rounded"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />

        <button
          type="submit"
          className="bg-black text-white px-4 py-2 rounded"
        >
          Submit Daily Log
        </button>
      </form>
    </div>
  );
}