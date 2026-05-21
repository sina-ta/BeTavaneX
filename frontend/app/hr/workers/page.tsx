"use client";

import { useEffect, useState } from "react";

import WorkersTable from "@/components/WorkersTable";

export default function WorkersPage() {

  const [workers, setWorkers] = useState([]);

  async function fetchWorkers() {

    const response = await fetch(
      "http://127.0.0.1:8000/workers"
    );

    const data = await response.json();

    setWorkers(data);
  }

  useEffect(() => {

    fetchWorkers();

  }, []);

  return (

    <div className="space-y-8">

      <h1 className="page-title">

        Workforce Management

      </h1>

      <div className="table-container">

        <h2 className="table-title">

          Workers Directory

        </h2>

        <WorkersTable workers={workers} />

      </div>

    </div>
  );
}