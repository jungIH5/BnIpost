"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { isAuthenticated } from "@/lib/auth";
import { userApi, postApi } from "@/lib/api";
import Navbar from "@/components/Navbar";
import PostForm from "@/components/PostForm";
import PostPreview from "@/components/PostPreview";
import type { User, PostResult } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User>();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PostResult | null>(null);
  const [isPreviewOnly, setIsPreviewOnly] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    userApi.getMe().then(setUser).catch(() => router.replace("/login"));
  }, [router]);

  const handleGenerate = async (formData: FormData) => {
    setLoading(true);
    setResult(null);
    setIsPreviewOnly(false);
    try {
      const res = await postApi.generate(formData);
      setResult(res);
      if (res.success) {
        toast.success("게시물이 성공적으로 게시되었습니다!");
      } else {
        toast.error(res.error || "게시 실패");
      }
    } catch {
      toast.error("서버 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = async (formData: FormData) => {
    setLoading(true);
    setResult(null);
    setIsPreviewOnly(true);
    try {
      const res = await postApi.preview(formData);
      setResult(res);
      if (!res.success) {
        toast.error(res.error || "미리보기 생성 실패");
      }
    } catch {
      toast.error("서버 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">게시물 자동 생성</h1>
          <p className="text-gray-500 mt-1 text-sm">
            키워드 또는 이미지를 입력하면 AI가 최적화된 게시물을 생성합니다.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PostForm
            onGenerate={handleGenerate}
            onPreview={handlePreview}
            loading={loading}
          />

          <div>
            {loading && (
              <div className="card flex flex-col items-center justify-center h-64 text-gray-400">
                <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
                <p className="text-sm font-medium">AI가 게시물을 생성하는 중...</p>
                <p className="text-xs mt-1">잠시만 기다려주세요</p>
              </div>
            )}
            {!loading && result && (
              <PostPreview result={result} isPreviewOnly={isPreviewOnly} />
            )}
            {!loading && !result && (
              <div className="card flex flex-col items-center justify-center h-64 text-gray-300 border-dashed">
                <p className="text-sm">생성 결과가 여기에 표시됩니다</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
