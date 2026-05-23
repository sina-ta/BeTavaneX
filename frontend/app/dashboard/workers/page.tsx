"use client";

import { useEffect, useState } from "react";

import WorkersTable from "@/components/tables/WorkersTable";

import PageHeader from "@/components/ui/PageHeader";

import SectionCard from "@/components/ui/SectionCard";

export default function WorkersPage() {

  const [workers, setWorkers] =
    useState([]);

  async function fetchWorkers() {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/workers"
      );

      const data = await response.json();

      setWorkers(data);

    } catch (err) {

      console.log(err);

    }
  }

  useEffect(() => {

    fetchWorkers();

  }, []);

  return (

    <div className="page-wrapper">

      <PageHeader
        title="Workforce Management"
        subtitle="
          Manage active workers,
          crews and workforce
          operational performance
        "
      />

      <SectionCard
        title="Workers Directory"
      >

        <WorkersTable
          workers={workers}
        />

      </SectionCard>

    </div>
  );
}