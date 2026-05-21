import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "react-hot-toast";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "BnIpost - AI 소셜 미디어 게시물 생성기",
  description: "키워드나 사진 하나로 네이버 블로그, 인스타그램 게시물을 자동 생성합니다.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <Toaster position="top-right" />
        {children}
      </body>
    </html>
  );
}
