"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { isAuthenticated } from "@/lib/auth";
import { authApi } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const error = searchParams.get("error");

  useEffect(() => {
    if (isAuthenticated()) router.replace("/dashboard");
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="card max-w-md w-full mx-4 text-center">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">BnIpost</h1>
          <p className="text-gray-500 text-sm">
            키워드나 사진 하나로<br />
            AI가 소셜 미디어 게시물을 자동으로 생성해드립니다.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            {error === "naver_failed" && "네이버 로그인에 실패했습니다. 다시 시도해주세요."}
            {error === "instagram_failed" && "인스타그램 로그인에 실패했습니다. 비즈니스 계정인지 확인해주세요."}
          </div>
        )}

        <div className="space-y-3">
          <a
            href={authApi.getNaverLoginUrl()}
            className="flex items-center justify-center gap-3 w-full py-3 px-4 bg-naver text-white rounded-xl font-medium hover:opacity-90 transition-opacity"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M16.273 12.845L7.376 0H0v24h7.727V11.155L16.624 24H24V0h-7.727z"/>
            </svg>
            네이버로 로그인
          </a>

          <a
            href={authApi.getInstagramLoginUrl()}
            className="flex items-center justify-center gap-3 w-full py-3 px-4 bg-gradient-to-r from-purple-500 via-pink-500 to-instagram text-white rounded-xl font-medium hover:opacity-90 transition-opacity"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
            </svg>
            인스타그램으로 로그인
          </a>
        </div>

        <p className="mt-6 text-xs text-gray-400">
          인스타그램 로그인은 비즈니스/크리에이터 계정만 지원됩니다.
        </p>
      </div>
    </div>
  );
}
