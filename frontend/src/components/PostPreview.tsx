"use client";

import { ExternalLink, CheckCircle, XCircle } from "lucide-react";
import type { PostResult } from "@/types";

interface PostPreviewProps {
  result: PostResult;
  isPreviewOnly?: boolean;
}

export default function PostPreview({ result, isPreviewOnly = false }: PostPreviewProps) {
  if (!result.success) {
    return (
      <div className="card border-red-200 bg-red-50">
        <div className="flex items-center gap-2 text-red-600 mb-2">
          <XCircle size={20} />
          <span className="font-semibold">생성 실패</span>
        </div>
        <p className="text-red-500 text-sm">{result.error}</p>
      </div>
    );
  }

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {!isPreviewOnly && result.published_url ? (
            <>
              <CheckCircle size={20} className="text-green-500" />
              <span className="font-semibold text-green-600">게시 완료</span>
            </>
          ) : (
            <span className="font-semibold text-gray-700">미리보기</span>
          )}
        </div>
        {result.published_url && (
          <a
            href={result.published_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-sm text-blue-600 hover:underline"
          >
            게시물 보기
            <ExternalLink size={14} />
          </a>
        )}
      </div>

      {result.generated_title && (
        <div>
          <p className="text-xs font-medium text-gray-500 mb-1 uppercase tracking-wide">제목</p>
          <p className="font-semibold text-gray-900">{result.generated_title}</p>
        </div>
      )}

      {result.generated_content && (
        <div>
          <p className="text-xs font-medium text-gray-500 mb-1 uppercase tracking-wide">본문</p>
          <div className="bg-gray-50 rounded-xl p-4 text-sm text-gray-700 whitespace-pre-wrap max-h-80 overflow-y-auto leading-relaxed">
            {result.generated_content}
          </div>
        </div>
      )}

      {result.generated_hashtags && result.generated_hashtags.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 mb-2 uppercase tracking-wide">해시태그</p>
          <div className="flex flex-wrap gap-1.5">
            {result.generated_hashtags.map((tag, i) => (
              <span
                key={i}
                className="px-2.5 py-1 bg-blue-50 text-blue-600 rounded-full text-xs font-medium"
              >
                #{tag.replace(/^#/, "")}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
