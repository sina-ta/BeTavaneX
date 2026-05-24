import OperationalSummarySection from "@/components/dashboard/OperationalSummarySection";
import TasksTable from "@/components/tables/TasksTable";
import CompactCard from "@/components/layout/primitives/CompactCard";
import type { DashboardTask } from "@/types/dashboard";

type TasksSectionProps = {
  tasks: DashboardTask[];
};

export default function TasksSection({
  tasks,
}: TasksSectionProps) {
  return (
    <section className="dashboard-tasks-section">
      <OperationalSummarySection tasks={tasks} />

      <CompactCard title="Work Units & Tasks">
        <TasksTable tasks={tasks} />
      </CompactCard>
    </section>
  );
}
