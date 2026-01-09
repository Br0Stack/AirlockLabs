/*
Author       : 
Template Name: 
Version      : 1.0
*/

jQuery(function($) {
	"use strict";

		/*START MENU JS*/
		$(window).on('scroll', function() {
			if ($(".navbar").offset().top > 50) {
				$(".navbar-fixed-top").addClass("top-nav-collapse");
			} else {
				$(".navbar-fixed-top").removeClass("top-nav-collapse");
			}
		});
		
		$('a.page-scroll').on('click', function(event) {
			var $anchor = $(this);
			$('html, body').stop().animate({
				scrollTop: $($anchor.attr('href')).offset().top - 10 
			}, 1500, 'easeInOutExpo');
			event.preventDefault();
		});

		/* Closes the Responsive Menu on Menu Item Click*/
		$('.navbar-collapse ul li a').on('click', function() {
			$('.navbar-toggle:visible').click();
		});
		/*END MENU JS*/ 

	  
	/*START WOW ANIMATIONS JS*/ 
		new WOW().init();
	/*END WOW ANIMATIONS JS*/ 
	
	
	function init_navbar() {
	var a = $("#masthead")
		, b = $(a).outerHeight();
	$(".site-header-affix-wrapper").css("height", b);
	var c;
	c = $(".topbar").outerHeight(), $(window).scroll(function () {
		$(window).scrollTop() > c ? $(a).addClass("sticky-bar").addClass("header-dark") : $(a).removeClass("sticky-bar").removeClass("header-dark")
	}), $(window).scrollTop() > c && $(a).addClass("sticky-bar").addClass("header-dark"), $(".nav-menu li a, .site-title a").on("click", function (a) {
		var b = $(this);
		$("html, body").stop().animate({
			scrollTop: $(b.attr("href")).offset().top
		}, 1500, "easeInOutExpo"), a.preventDefault()
	}), $(".nav-menu li").on("click", function () {
		$(".nav-menu li.current-menu-item").removeClass("current-menu-item"), $(this).addClass("current-menu-item")
	})
}


jQuery(window).trigger("resize").trigger("scroll"), init_navbar()

	const rulesMatrix = [
		{
			key: "offline_access",
			name: "Offline access",
			triggerLogic: "Access event recorded while the device reports no network connectivity.",
			severity: "High",
			explanationTemplate: "Access event {{eventId}} occurred while the device was offline for {{offlineMinutes}} minutes.",
			evaluate: (context) => {
				const offlineEvents = context.accessEvents.filter((event) => event.offline === true);

				if (!offlineEvents.length) {
					return [];
				}

				return [
					buildAnomaly({
						rule: "Offline access",
						severity: "High",
						supportingEvents: offlineEvents,
						whyUnusual: "Access was logged while the device reported an offline state, which is atypical for authenticated sessions.",
						whyItMatters: "Offline access can indicate tampering with device logs or gaps in network telemetry during sensitive activity.",
						corroborationReferences: [
							"Device status log: offline state transitions",
							`Access events: ${offlineEvents.map((event) => event.id).join(", ")}`
						]
					})
				];
			}
		},
		{
			key: "new_device",
			name: "New device",
			triggerLogic: "Access event originates from a device that is not in the known device roster.",
			severity: "High",
			explanationTemplate: "Device {{deviceId}} accessed the system without a prior enrollment record.",
			evaluate: (context) => {
				const newDeviceEvents = context.accessEvents.filter(
					(event) => !context.knownDevices.includes(event.deviceId)
				);

				if (!newDeviceEvents.length) {
					return [];
				}

				return [
					buildAnomaly({
						rule: "New device",
						severity: "High",
						supportingEvents: newDeviceEvents,
						whyUnusual: "Access occurred from a device that does not appear in the historical device roster.",
						whyItMatters: "Unrecognized devices can signal account compromise or unauthorized device enrollment attempts.",
						corroborationReferences: [
							"Device inventory: known device list",
							`Access events: ${newDeviceEvents.map((event) => `${event.id} (${event.deviceId})`).join(", ")}`
						]
					})
				];
			}
		},
		{
			key: "geo_jump",
			name: "Geo jumps",
			triggerLogic: "Consecutive access events imply travel beyond plausible speed thresholds.",
			severity: "Medium",
			explanationTemplate: "Access moved from {{fromLocation}} to {{toLocation}} in {{hours}} hours.",
			evaluate: (context) => {
				const jumpPairs = [];
				const sortedEvents = [...context.accessEvents].sort(
					(a, b) => new Date(a.timestamp) - new Date(b.timestamp)
				);

				for (let index = 1; index < sortedEvents.length; index += 1) {
					const previous = sortedEvents[index - 1];
					const current = sortedEvents[index];
					const hours = hoursBetween(previous.timestamp, current.timestamp);
					const distanceKm = haversineKm(previous.location, current.location);

					if (distanceKm > context.geoJumpThresholdKm && hours < context.geoJumpThresholdHours) {
						jumpPairs.push({ previous, current, distanceKm, hours });
					}
				}

				if (!jumpPairs.length) {
					return [];
				}

				const supportingEvents = jumpPairs.flatMap((pair) => [pair.previous, pair.current]);

				return [
					buildAnomaly({
						rule: "Geo jumps",
						severity: "Medium",
						supportingEvents,
						whyUnusual: "Access locations shift faster than expected travel time between consecutive events.",
						whyItMatters: "Rapid geo changes can indicate VPN spoofing, credential sharing, or anomalous routing.",
						corroborationReferences: [
							"IP geolocation timeline",
							`Jump pairs: ${jumpPairs
								.map(
									(pair) =>
										`${pair.previous.location.label} → ${pair.current.location.label} (${pair.distanceKm.toFixed(
											0
										)} km in ${pair.hours.toFixed(1)}h)`
								)
								.join("; ")}`
						]
					})
				];
			}
		},
		{
			key: "nighttime_spike",
			name: "Nighttime spikes",
			triggerLogic: "Night-hour activity exceeds the expected nightly baseline.",
			severity: "Medium",
			explanationTemplate: "Nighttime activity reached {{eventCount}} events versus a baseline of {{baseline}}.",
			evaluate: (context) => {
				const nightEvents = context.accessEvents.filter((event) =>
					isNightHour(event.timestamp, context.nightHours)
				);
				const nightCountsByDay = nightEvents.reduce((accumulator, event) => {
					const day = event.timestamp.split("T")[0];
					accumulator[day] = accumulator[day] ? accumulator[day] + 1 : 1;
					return accumulator;
				}, {});

				const spikeDays = Object.keys(nightCountsByDay).filter(
					(day) => nightCountsByDay[day] > context.nightBaseline
				);

				if (!spikeDays.length) {
					return [];
				}

				const supportingEvents = nightEvents.filter((event) =>
					spikeDays.includes(event.timestamp.split("T")[0])
				);

				return [
					buildAnomaly({
						rule: "Nighttime spikes",
						severity: "Medium",
						supportingEvents,
						whyUnusual: "Night-hour access volume exceeded the expected baseline for typical user activity.",
						whyItMatters: "Spikes outside normal hours can indicate automated access or unauthorized use after hours.",
						corroborationReferences: [
							"Behavior baseline: nightly access frequency",
							`Nighttime events: ${supportingEvents.map((event) => event.id).join(", ")}`
						]
					})
				];
			}
		},
		{
			key: "restricted_window",
			name: "Access during travel/incarceration windows",
			triggerLogic: "Access falls inside known travel or incarceration blackout windows.",
			severity: "High",
			explanationTemplate: "Access event {{eventId}} occurred during {{windowType}} window ({{windowLabel}}).",
			evaluate: (context) => {
				const flagged = context.accessEvents
					.map((event) => ({
						event,
						window: findRestrictedWindow(event.timestamp, context.restrictedWindows)
					}))
					.filter((entry) => entry.window);

				if (!flagged.length) {
					return [];
				}

				const supportingEvents = flagged.map((entry) => entry.event);

				return [
					buildAnomaly({
						rule: "Access during travel/incarceration windows",
						severity: "High",
						supportingEvents,
						whyUnusual: "Access was recorded while the subject should have been unavailable due to travel or incarceration.",
						whyItMatters: "Activity during restricted windows may indicate credential sharing or timeline inconsistencies.",
						corroborationReferences: [
							"Travel/incarceration calendar",
							`Restricted window events: ${flagged
								.map(
									(entry) =>
										`${entry.event.id} (${entry.window.type}: ${entry.window.label})`
								)
								.join(", ")}`
						]
					})
				];
			}
		},
		{
			key: "expected_gaps",
			name: "Expected gaps",
			triggerLogic: "Observed inactivity gap exceeds the expected cadence window.",
			severity: "Low",
			explanationTemplate: "Gap of {{gapHours}} hours exceeded the expected {{expectedGap}}-hour cadence.",
			evaluate: (context) => {
				const sortedEvents = [...context.accessEvents].sort(
					(a, b) => new Date(a.timestamp) - new Date(b.timestamp)
				);
				const gaps = [];

				for (let index = 1; index < sortedEvents.length; index += 1) {
					const previous = sortedEvents[index - 1];
					const current = sortedEvents[index];
					const gapHours = hoursBetween(previous.timestamp, current.timestamp);

					if (gapHours > context.expectedGapHours) {
						gaps.push({ previous, current, gapHours });
					}
				}

				if (!gaps.length) {
					return [];
				}

				const supportingEvents = gaps.flatMap((gap) => [gap.previous, gap.current]);

				return [
					buildAnomaly({
						rule: "Expected gaps",
						severity: "Low",
						supportingEvents,
						whyUnusual: "Access inactivity lasted longer than the expected cadence for this account.",
						whyItMatters: "Extended gaps can indicate missing telemetry, device outages, or abrupt behavior changes.",
						corroborationReferences: [
							"Expected cadence policy",
							`Gap boundaries: ${gaps
								.map(
									(gap) =>
										`${gap.previous.id} → ${gap.current.id} (${gap.gapHours.toFixed(
											1
										)}h)`
								)
								.join(", ")}`
						]
					})
				];
			}
		}
	];

	const analysisContext = {
		knownDevices: ["dev-001", "dev-002", "dev-003"],
		nightBaseline: 1,
		nightHours: { start: 0, end: 5 },
		geoJumpThresholdKm: 500,
		geoJumpThresholdHours: 3,
		expectedGapHours: 12,
		restrictedWindows: [
			{
				type: "travel",
				label: "Client visit - Chicago",
				start: "2024-06-11T00:00:00Z",
				end: "2024-06-12T23:59:00Z"
			},
			{
				type: "incarceration",
				label: "Custody window - June 2024",
				start: "2024-06-14T00:00:00Z",
				end: "2024-06-15T23:59:00Z"
			}
		],
		accessEvents: [
			{
				id: "evt-1001",
				timestamp: "2024-06-10T02:15:00Z",
				deviceId: "dev-004",
				offline: true,
				location: { label: "New York, NY", lat: 40.7128, lon: -74.006 },
				ip: "203.0.113.50"
			},
			{
				id: "evt-1002",
				timestamp: "2024-06-10T02:42:00Z",
				deviceId: "dev-004",
				offline: true,
				location: { label: "New York, NY", lat: 40.7128, lon: -74.006 },
				ip: "203.0.113.50"
			},
			{
				id: "evt-1003",
				timestamp: "2024-06-10T04:12:00Z",
				deviceId: "dev-002",
				offline: false,
				location: { label: "Newark, NJ", lat: 40.7357, lon: -74.1724 },
				ip: "198.51.100.12"
			},
			{
				id: "evt-1004",
				timestamp: "2024-06-10T07:30:00Z",
				deviceId: "dev-002",
				offline: false,
				location: { label: "Newark, NJ", lat: 40.7357, lon: -74.1724 },
				ip: "198.51.100.12"
			},
			{
				id: "evt-1005",
				timestamp: "2024-06-10T09:30:00Z",
				deviceId: "dev-001",
				offline: false,
				location: { label: "Chicago, IL", lat: 41.8781, lon: -87.6298 },
				ip: "192.0.2.25"
			},
			{
				id: "evt-1006",
				timestamp: "2024-06-11T01:10:00Z",
				deviceId: "dev-001",
				offline: false,
				location: { label: "Chicago, IL", lat: 41.8781, lon: -87.6298 },
				ip: "192.0.2.25"
			},
			{
				id: "evt-1007",
				timestamp: "2024-06-14T03:20:00Z",
				deviceId: "dev-002",
				offline: false,
				location: { label: "Boston, MA", lat: 42.3601, lon: -71.0589 },
				ip: "198.51.100.85"
			},
			{
				id: "evt-1008",
				timestamp: "2024-06-16T08:00:00Z",
				deviceId: "dev-003",
				offline: false,
				location: { label: "Boston, MA", lat: 42.3601, lon: -71.0589 },
				ip: "198.51.100.85"
			}
		]
	};

	function buildAnomaly({ rule, severity, supportingEvents, whyUnusual, whyItMatters, corroborationReferences }) {
		return {
			ruleName: rule,
			severity,
			supportingEvents,
			whyUnusual,
			whyItMatters,
			corroborationReferences,
			confidence: computeConfidence(supportingEvents.length)
		};
	}

	function computeConfidence(eventCount) {
		if (eventCount >= 5) {
			return { label: "High", score: 0.9, supportingEvents: eventCount };
		}
		if (eventCount >= 3) {
			return { label: "Medium", score: 0.7, supportingEvents: eventCount };
		}
		return { label: "Low", score: 0.45, supportingEvents: eventCount };
	}

	function hoursBetween(start, end) {
		return Math.abs(new Date(end) - new Date(start)) / (1000 * 60 * 60);
	}

	function haversineKm(start, end) {
		const toRadians = (value) => (value * Math.PI) / 180;
		const radius = 6371;
		const latDelta = toRadians(end.lat - start.lat);
		const lonDelta = toRadians(end.lon - start.lon);
		const lat1 = toRadians(start.lat);
		const lat2 = toRadians(end.lat);

		const a =
			Math.sin(latDelta / 2) * Math.sin(latDelta / 2) +
			Math.sin(lonDelta / 2) * Math.sin(lonDelta / 2) * Math.cos(lat1) * Math.cos(lat2);
		const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
		return radius * c;
	}

	function isNightHour(timestamp, nightHours) {
		const hour = new Date(timestamp).getUTCHours();
		return hour >= nightHours.start && hour <= nightHours.end;
	}

	function findRestrictedWindow(timestamp, windows) {
		const moment = new Date(timestamp).getTime();
		return windows.find((window) => {
			const start = new Date(window.start).getTime();
			const end = new Date(window.end).getTime();
			return moment >= start && moment <= end;
		});
	}

	function renderRulesMatrix(rules) {
		const tableBody = document.querySelector("#rules-matrix tbody");
		if (!tableBody) {
			return;
		}
		tableBody.innerHTML = "";
		rules.forEach((rule) => {
			const row = document.createElement("tr");
			row.innerHTML = `
				<td>${rule.name}</td>
				<td>${rule.triggerLogic}</td>
				<td>${rule.severity}</td>
				<td>${rule.explanationTemplate}</td>
			`;
			tableBody.appendChild(row);
		});
	}

	function renderAnomalies(anomalies) {
		const container = document.getElementById("anomaly-results");
		if (!container) {
			return;
		}
		container.innerHTML = "";
		anomalies.forEach((anomaly, index) => {
			const panel = document.createElement("div");
			panel.className = "panel panel-default";
			panel.innerHTML = `
				<div class="panel-heading">
					<h4 class="panel-title">${anomaly.ruleName} <small>(${anomaly.severity} severity)</small></h4>
				</div>
				<div class="panel-body">
					<p><strong>Why unusual:</strong> ${anomaly.whyUnusual}</p>
					<p><strong>Why it matters:</strong> ${anomaly.whyItMatters}</p>
					<p><strong>Corroboration references:</strong></p>
					<ul>
						${anomaly.corroborationReferences.map((reference) => `<li>${reference}</li>`).join("")}
					</ul>
					<p><strong>Confidence:</strong> ${anomaly.confidence.label} (${anomaly.confidence.supportingEvents} supporting events)</p>
				</div>
			`;
			panel.setAttribute("data-anomaly-index", index.toString());
			container.appendChild(panel);
		});
	}

	const anomalies = rulesMatrix.flatMap((rule) => rule.evaluate(analysisContext));
	renderRulesMatrix(rulesMatrix);
	renderAnomalies(anomalies);

  });
