"use client";

import { useState, useRef } from "react";
import { ImagePlus, X, Send, Eye } from "lucide-react";
import clsx from "clsx";
import type { Platform } from "@/types";

interface PostFormProps {
  onGenerate: (formData: FormData) => Promise<void>;
  onPreview: (formData: FormData) => Promise<void>;
  loading: boolean;
}

export default function PostForm({ onGenerate, onPreview, loading }: PostFormProps) {
  const [platform, setPlatform] = useState<Platform>("naver");
  const [keyword, setKeyword] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setImagePreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const removeImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const buildFormData = (): FormData => {
    const fd = new FormData();
    fd.append("platform", platform);
    if (keyword.trim()) fd.append("keyword", keyword.trim());
    if (imageFile) fd.append("image", imageFile);
    return fd;
  };

  const isValid = keyword.trim() || imageFile;

  return (
    <div className="card space-y-5">
      <h2 className="text-lg font-semibold">게시물 생성</h2>

      {/* Platform selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">플랫폼 선택</label>
        <div className="flex gap-3">
          {(["naver", "instagram"] as Platform[]).map((p) => (
            <button
              key={p}
              onClick={() => setPlatform(p)}
              className={clsx(
                "flex-1 py-2.5 rounded-xl text-sm font-medium border-2 transition-all",
                platform === p
                  ? p === "naver"
                    ? "border-naver bg-green-50 text-naver"
                    : "border-instagram bg-pink-50 text-instagram"
                  : "border-gray-200 text-gray-500 hover:border-gray-300"
              )}
            >
              {p === "naver" ? "네이버 블로그" : "인스타그램"}
            </button>
          ))}
        </div>
      </div>

      {/* Keyword input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          키워드 <span className="text-gray-400 font-normal">(이미지 업로드 시 생략 가능)</span>
        </label>
        <textarea
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="예: 제주도 카페 감성 여행, 여름 신상 원피스 홍보, 건강 식단 추천..."
          className="input-field h-24"
          disabled={loading}
        />
      </div>

      {/* Image upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          이미지 <span className="text-gray-400 font-normal">(선택)</span>
        </label>
        {imagePreview ? (
          <div className="relative inline-block">
            <img
              src={imagePreview}
              alt="preview"
              className="h-40 w-auto rounded-xl object-cover border border-gray-200"
            />
            <button
              onClick={removeImage}
              className="absolute -top-2 -right-2 bg-white border border-gray-200 rounded-full p-1 shadow-sm hover:bg-red-50"
            >
              <X size={14} className="text-gray-500" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 px-4 py-3 border-2 border-dashed border-gray-200 rounded-xl text-gray-400 hover:border-blue-300 hover:text-blue-400 transition-colors text-sm"
            disabled={loading}
          >
            <ImagePlus size={18} />
            이미지 업로드 (JPG, PNG, WEBP)
          </button>
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleImageChange}
          className="hidden"
        />
      </div>

      {/* Action buttons */}
      <div className="flex gap-3 pt-2">
        <button
          onClick={() => onPreview(buildFormData())}
          disabled={!isValid || loading}
          className="btn-secondary flex items-center gap-2"
        >
          <Eye size={16} />
          미리보기
        </button>
        <button
          onClick={() => onGenerate(buildFormData())}
          disabled={!isValid || loading}
          className="btn-primary flex items-center gap-2 flex-1 justify-center"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              AI 생성 중...
            </>
          ) : (
            <>
              <Send size={16} />
              생성 후 게시하기
            </>
          )}
        </button>
      </div>
    </div>
  );
}
