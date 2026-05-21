"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/auth";
import { userApi, historyApi } from "@/lib/api";
import Navbar from "@/components/Navbar";
import { ExternalLink, CheckCircle, XCircle, Clock, RefreshCw } from "lucide-react";
import clsx from "clsx";
import type { User, HistoryItem, Platform } from "@/types";

const STATUS_CONFIG = {
  published: { icon: CheckCircle, color: "text-green-500", label: "게시됨" },
  failed: { icon: XCircle, color: "text-red-500", label: "실패" },
  pending: { icon: Clock, color: "text-yellow-500", label: "대기중" },
  processing: { icon: RefreshCw, color: "text-blue-500", label: "처리중" },
};

export default function HistoryPage() {
  const router = useRouter();
  const [user, setUser] = useState<User>();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [platform, setPlatform] = useState<Platform | "all">("all");
  const [page, setPage] = useState(1);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) { router.replace("/login"); return; }
    userApi.getMe().then(setUser).catch(() => router.replace("/login"));
  }, [router]);

  useEffect(() => {
    setLoading(true);
    historyApi
      .getHistory(page, platform === "all" ? undefined : platform)
      .then(setHistory)
      .finally(() => setLoading(false));
  }, [page, platform]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">게시 이력</h1>
            <p className="text-gray-500 mt-1 text-sm">AI가 생성하고 게시한 게시물 목록</p>
          </div>
          <div className="flex gap-2">
            {(["all", "naver", "instagram"] as const).map((p) => (
              <button
                key={p}
                onClick={() => { setPlatform(p); setPage(1); }}
                className={clsx(
                  "px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                  platform === p ? "bg-blue-600 text-white" : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
                )}
              >
                {p === "all" ? "전체" : p === "naver" ? "네이버" : "인스타그램"}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : history.length === 0 ? (
          <div className="card text-center py-16 text-gray-400">
            <p>아직 게시 이력이 없습니다.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {history.map((item) => {
              const status = STATUS_CONFIG[item.status];
              const StatusIcon = status.icon;
              const isOpen = expanded === item.id;

              return (
                <div key={item.id} className="card cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => setExpanded(isOpen ? null : item.id)}>
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3 min-w-0">
                      <StatusIcon size={18} className={status.color} />
                      <div className="min-w-0">
                        <p className="font-medium text-gray-900 truncate">
                          {item.generated_title || item.input_keyword || "(이미지 입력)"}
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          {item.platform === "naver" ? "네이버 블로그" : "인스타그램"} · {status.label}
                          {item.created_at && ` · ${new Date(item.created_at).toLocaleDateString("ko-KR")}`}
                        </p>
                      </div>
                    </div>
                    {item.published_url && (
                      <a
                        href={item.published_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="flex-shrink-0 flex items-center gap-1 text-xs text-blue-600 hover:underline"
                      >
                        보기 <ExternalLink size={12} />
                      </a>
                    )}
                  </div>

                  {isOpen && (
                    <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                      {item.generated_content && (
                        <div>
                          <p className="text-xs text-gray-400 mb-1">본문</p>
                          <p className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 rounded-lg p-3 max-h-48 overflow-y-auto">
                            {item.generated_content}
                          </p>
                        </div>
                      )}
                      {item.generated_hashtags && item.generated_hashtags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {item.generated_hashtags.map((tag, i) => (
                            <span key={i} className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full text-xs">
                              #{tag.replace(/^#/, "")}
                            </span>
                          ))}
                        </div>
                      )}
                      {item.error_message && (
                        <p className="text-xs text-red-500 bg-red-50 rounded-lg p-2">{item.error_message}</p>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Pagination */}
        {history.length > 0 && (
          <div className="flex justify-center gap-2 mt-6">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
              className="btn-secondary px-3 py-1.5 text-sm disabled:opacity-40">이전</button>
            <span className="px-3 py-1.5 text-sm text-gray-600">{page} 페이지</span>
            <button onClick={() => setPage(p => p + 1)} disabled={history.length < 10}
              className="btn-secondary px-3 py-1.5 text-sm disabled:opacity-40">다음</button>
          </div>
        )}
      </main>
    </div>
  );
}
