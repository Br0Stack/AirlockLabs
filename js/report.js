(function () {
	"use strict";

	function getTextContent(selector) {
		var element = document.querySelector(selector);
		return element ? element.textContent.trim() : "";
	}

	function getListItems(selector) {
		return Array.prototype.slice.call(document.querySelectorAll(selector)).map(function (item) {
			return item.textContent.trim();
		});
	}

	function getAppendixRows() {
		var rows = Array.prototype.slice.call(document.querySelectorAll("#report-appendix tbody tr"));
		return rows.map(function (row) {
			var cells = row.querySelectorAll("td");
			return {
				itemId: cells[0] ? cells[0].textContent.trim() : "",
				description: cells[1] ? cells[1].textContent.trim() : "",
				owner: cells[2] ? cells[2].textContent.trim() : "",
				timestampUtc: cells[3] ? cells[3].textContent.trim() : "",
				reference: cells[4] ? cells[4].textContent.trim() : ""
			};
		});
	}

	function buildReportData() {
		return {
			executiveSummary: getTextContent("#report-content .report-block:nth-of-type(1) p"),
			keyFindings: getListItems("#report-content .report-block:nth-of-type(2) li"),
			timelineExcerpts: getListItems("#report-content .report-block:nth-of-type(3) li"),
			corroboratingSources: getListItems("#report-content .report-block:nth-of-type(4) li"),
			appendix: getAppendixRows(),
			footerDisclaimer: getTextContent("#report-content .report-footer p")
		};
	}

	function downloadBlob(blob, filename) {
		var url = URL.createObjectURL(blob);
		var link = document.createElement("a");
		link.href = url;
		link.download = filename;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		URL.revokeObjectURL(url);
	}

	function exportJson() {
		var reportData = buildReportData();
		var blob = new Blob([JSON.stringify(reportData, null, 2)], { type: "application/json" });
		downloadBlob(blob, "investigation-report.json");
	}

	function exportCsv() {
		var rows = getAppendixRows();
		var header = ["Item ID", "Description", "Owner", "Timestamp (UTC)", "Reference"];
		var csvLines = [header.join(",")];
		rows.forEach(function (row) {
			var line = [row.itemId, row.description, row.owner, row.timestampUtc, row.reference]
				.map(function (value) {
					var escaped = String(value).replace(/"/g, '""');
					return "\"" + escaped + "\"";
				})
				.join(",");
			csvLines.push(line);
		});
		var blob = new Blob([csvLines.join("\n")], { type: "text/csv" });
		downloadBlob(blob, "report-appendix.csv");
	}

	function addPdfSection(doc, title, lines, y, pageHeight, margin, lineHeight) {
		var currentY = y;
		doc.setFont("helvetica", "bold");
		doc.text(title, margin, currentY);
		currentY += lineHeight;
		doc.setFont("helvetica", "normal");
		lines.forEach(function (line) {
			if (currentY > pageHeight - margin) {
				doc.addPage();
				currentY = margin;
			}
			doc.text(line, margin, currentY);
			currentY += lineHeight;
		});
		return currentY + lineHeight * 0.5;
	}

	function exportPdf() {
		if (!window.jspdf || !window.jspdf.jsPDF) {
			return;
		}
		var reportData = buildReportData();
		var doc = new window.jspdf.jsPDF({ unit: "pt", format: "letter" });
		var margin = 40;
		var lineHeight = 16;
		var pageHeight = doc.internal.pageSize.getHeight();
		var y = margin;

		doc.setFont("helvetica", "bold");
		doc.setFontSize(18);
		doc.text("Investigation Report", margin, y);
		y += 30;
		doc.setFontSize(12);

		y = addPdfSection(doc, "Executive Summary", doc.splitTextToSize(reportData.executiveSummary, 520), y, pageHeight, margin, lineHeight);
		y = addPdfSection(doc, "Key Findings", reportData.keyFindings, y, pageHeight, margin, lineHeight);
		y = addPdfSection(doc, "Timeline Excerpts", reportData.timelineExcerpts, y, pageHeight, margin, lineHeight);
		y = addPdfSection(doc, "Corroborating Sources", reportData.corroboratingSources, y, pageHeight, margin, lineHeight);

		var appendixLines = reportData.appendix.map(function (row) {
			return row.itemId + " | " + row.description + " | " + row.owner + " | " + row.timestampUtc + " | " + row.reference;
		});
		y = addPdfSection(doc, "Appendix", appendixLines, y, pageHeight, margin, lineHeight);
		addPdfSection(doc, "Report Footer", doc.splitTextToSize(reportData.footerDisclaimer, 520), y, pageHeight, margin, lineHeight);

		doc.save("investigation-report.pdf");
	}

	function handleExport(event) {
		var target = event.target;
		if (!target.classList.contains("report-export")) {
			return;
		}
		var type = target.getAttribute("data-export");
		switch (type) {
			case "pdf":
				exportPdf();
				break;
			case "csv":
				exportCsv();
				break;
			case "json":
				exportJson();
				break;
			default:
				break;
		}
	}

	document.addEventListener("click", handleExport);
})();
