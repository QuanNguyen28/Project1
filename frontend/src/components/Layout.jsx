import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

export default function Layout() {
  return (
    <div className="h-screen w-full bg-[var(--app-bg,#0b1220)] text-[var(--fg,#e5e7eb)]">
      <div className="grid h-full grid-cols-[320px_minmax(0,1fr)]">
        <aside className="h-full w-[320px] shrink-0">
          <Sidebar />
        </aside>

        <section className="flex min-w-0 flex-col overflow-hidden">
          <Topbar />

          <main className="mx-auto w-full max-w-[1560px] 2xl:max-w-[1720px] px-8 lg:px-12 py-6 lg:py-8">
            <Outlet />
          </main>
        </section>
      </div>
    </div>
  );
}
