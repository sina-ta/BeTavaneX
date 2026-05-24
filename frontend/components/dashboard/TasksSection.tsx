import TasksTable from "@/components/tables/TasksTable";
import type { DashboardTask } from "@/types/dashboard";

type TasksSectionProps = {
  tasks: DashboardTask[];
};

export default function TasksSection({
  tasks,
}: TasksSectionProps) {
  return <TasksTable tasks={tasks} />;
}
