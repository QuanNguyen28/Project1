# Báo cáo LaTeX Project 1

Biên dịch bằng XeLaTeX để hỗ trợ tiếng Việt và Times New Roman:

```powershell
cd report
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

Trước khi nộp, sửa các biến ở đầu `main.tex`:

- `StudentName`
- `StudentID`
- `ClassName`
- `Supervisor`
- `Semester`
- `PlaceAndDate`

Sau khi sửa thông tin, biên dịch hai lần để cập nhật mục lục, danh mục hình, bảng và tham chiếu chéo.
