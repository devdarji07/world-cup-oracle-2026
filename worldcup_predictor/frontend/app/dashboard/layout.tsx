import { DashboardNav } from "../../components/DashboardNav";
export default function DashboardLayout({children}:{children:React.ReactNode}){return <main className="min-h-screen bg-[#050509] px-5 py-4 text-white"><DashboardNav/>{children}</main>}
