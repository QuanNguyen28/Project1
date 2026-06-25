import React, { useMemo } from "react";
import { marked } from "marked";
import DOMPurify from "dompurify";
import {
  BriefcaseBusiness,
  Building2,
  ClipboardCheck,
  FileText,
  Globe2,
  MapPin,
  Sparkles,
} from "lucide-react";

marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: false,
  mangle: false,
});

function stripFirstHeading(markdown = "") {
  return markdown.replace(/^\s*#\s+.+(?:\r?\n)+/, "").trim();
}

function pickTitle(markdown = "", fallback = "") {
  const firstHeading = markdown.match(/^\s*#\s+(.+?)\s*$/m)?.[1];
  return (fallback || firstHeading || "Job Description").trim();
}

function isProbablyEmpty(markdown = "") {
  return !markdown || !markdown.trim();
}

function MetaChip({ icon: Icon, children }) {
  if (!children) return null;
  return (
    <span className="jd-meta-chip">
      <Icon className="size-3.5" />
      {children}
    </span>
  );
}

export default function PreviewPanel({
  markdown,
  jd,
  title,
  meta = {},
  className = "",
}) {
  const empty = isProbablyEmpty(markdown);
  const headerTitle = pickTitle(markdown, title || jd?.title);

  const html = useMemo(() => {
    if (empty) return "";
    const withoutDuplicateTitle = stripFirstHeading(markdown);
    const raw = marked.parse(withoutDuplicateTitle || markdown || "");
    return DOMPurify.sanitize(raw, {
      USE_PROFILES: { html: true },
      ADD_ATTR: ["target", "rel"],
    });
  }, [markdown, empty]);

  const wordCount = useMemo(() => {
    if (empty) return 0;
    return markdown.trim().split(/\s+/).filter(Boolean).length;
  }, [markdown, empty]);

  return (
    <article className={`jd-preview-shell ${className}`}>
      <div className="jd-preview-toolbar">
        <div className="flex items-center gap-2">
          <span className="jd-live-dot" />
          <span>Live JD preview</span>
        </div>
        <div className="hidden sm:flex items-center gap-2 text-xs">
          {jd?.jd_id ? <span>JD #{jd.jd_id}</span> : null}
          {meta.version ? <span>v{meta.version}</span> : null}
          <span>{wordCount} words</span>
        </div>
      </div>

      <div className="jd-document">
        <header className="jd-hero">
          <div className="jd-kicker">
            <Sparkles className="size-4" />
            SmartHire Composer
          </div>

          <h1>{headerTitle}</h1>

          <div className="jd-meta-grid">
            <MetaChip icon={Building2}>{meta.department}</MetaChip>
            <MetaChip icon={BriefcaseBusiness}>{meta.jobFamily}</MetaChip>
            <MetaChip icon={ClipboardCheck}>{meta.level}</MetaChip>
            <MetaChip icon={FileText}>{meta.employmentType}</MetaChip>
            <MetaChip icon={MapPin}>{meta.location}</MetaChip>
            <MetaChip icon={Globe2}>
              {meta.language === "vi" ? "Tiếng Việt" : "English"}
            </MetaChip>
          </div>
        </header>

        {empty ? (
          <div className="jd-empty-state">
            <div className="jd-empty-icon">
              <FileText className="size-7" />
            </div>
            <h2>Preview sẽ hiển thị tại đây</h2>
            <p>
              Nhập Markdown hoặc bấm Generate để tạo một JD có bố cục giống bản
              đăng tuyển thật: tiêu đề rõ, thông tin vai trò, trách nhiệm, yêu
              cầu và quyền lợi.
            </p>
          </div>
        ) : (
          <div
            className="jd-content"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        )}
      </div>
    </article>
  );
}
