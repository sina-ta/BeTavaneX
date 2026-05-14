"use client";

import { useState, useEffect } from "react";


type WorkUnit = {
  id: number;
  title: string;
  baseline: number;
  unit: string;
};

export default function WorkUnitsPage() {
  const [title, setTitle] = useState("");
  const [baseline, setBaseline] = useState<number | "">("");
  const [unit, setUnit] = useState("");
  const [data, setData] = useState<any[]>([]);
  const [workUnits, setWorkUnits] = useState<WorkUnit[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  useEffect(() => {
    fetch("http://127.0.0.1:8000/dashboard")
      .then((res) => res.json())
      .then((data) => setData(data.tasks));
  }, []);
  // 🔥 SORT + FILTER
  const [sortKey, setSortKey] = useState("final_score");
  const [sortAsc, setSortAsc] = useState(true);
  const [showCritical, setShowCritical] = useState(false);

  const resetForm = () => {
    setTitle("");
    setBaseline("");
    setUnit("");
    setEditingId(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!title || baseline === "" || !unit) return;

    if (editingId !== null) {
      setWorkUnits(
        workUnits.map((wu) =>
          wu.id === editingId
            ? { ...wu, title, baseline: Number(baseline), unit }
            : wu
        )
      );
    } else {
      setWorkUnits([
        ...workUnits,
        {
          id: Date.now(),
          title,
          baseline: Number(baseline),
          unit,
        },
      ]);
    }

    resetForm();
  };

  // 🔥 FILTER
  const filteredData = showCritical
    ? data.filter((d: any) => d.alert === "🔴 Critical")
    : data;

  // 🔥 SORT
  const sortedData = [...filteredData].sort((a: any, b: any) => {
    if (sortAsc) {
      return a[sortKey] > b[sortKey] ? 1 : -1;
    } else {
      return a[sortKey] < b[sortKey] ? 1 : -1;
    }
  });
  
  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">
        {editingId ? "Edit Work Unit" : "Create Work Unit"}
      </h1>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 bg-white p-6 rounded-2xl shadow-md border"
      >
        <input
          type="text"
          placeholder="Work Title"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        <input
          type="number"
          placeholder="Baseline Quantity"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={baseline}
          onChange={(e) =>
            setBaseline(e.target.value === "" ? "" : Number(e.target.value))
          }
        />

        <select
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"        
          value={unit}
          onChange={(e) => setUnit(e.target.value)}
        >
          <option value="">Select unit</option>
          <option value="m2">m²</option>
          <option value="m3">m³</option>
          <option value="ton">Ton</option>
          <option value="item">Item</option>
          <option value="hour">Hour</option>
          <option value="day">Day</option>
        </select>

        <button className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl font-semibold transition">
          {editingId ? "Update" : "Save"}
        </button>
      </form>   
    </div>
  );
}