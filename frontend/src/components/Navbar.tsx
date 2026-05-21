"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { logout } from "@/lib/auth";
import { LayoutDashboard, History, LogOut } from "lucide-react";
import clsx from "clsx";
import type { User } from "@/types";

interface NavbarProps {
  user?: User;
}

export default function Navbar({ user }: NavbarProps) {
  const pathname = usePathname();

  const navItems = [
    { href: "/dashboard", label: "게시물 생성", icon: LayoutDashboard },
    { href: "/history", label: "내 게시 이력", icon: History },
  ];

  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
      <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/dashboard" className="font-bold text-xl text-blue-600">
          BnIpost
        </Link>

        <nav className="flex items-center gap-1">
          {navItems.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                pathname === href
                  ? "bg-blue-50 text-blue-600"
                  : "text-gray-600 hover:bg-gray-100"
              )}
            >
              <Icon size={16} />
              {label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          {user && (
            <span className="text-sm text-gray-600 hidden sm:block">
              {user.nickname}
            </span>
          )}
          <button
            onClick={logout}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-red-500 transition-colors"
          >
            <LogOut size={16} />
            <span className="hidden sm:block">로그아웃</span>
          </button>
        </div>
      </div>
    </header>
  );
}
