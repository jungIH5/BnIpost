"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { setToken } from "@/lib/auth";

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      setToken(token);
      router.replace("/dashboard");
    } else {
      router.replace("/login?error=token_missing");
    }
  }, [router, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-500">로그인 처리 중...</p>
      </div>
    </div>
  );
}
