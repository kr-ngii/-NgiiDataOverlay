# 국토지리정보원 공간정보 중첩 검사 툴

## 본 툴의 목적
본 툴은 QGIS에서 플러그인으로 동작하는 프로그램입니다. 때문에 QGIS 의 설치가 기본적으로 필요하고, 기초자료/수정성과 비교기능을 쓰기 위해서는 PostgreSQL과 PostGIS의 설치도 필요합니다.

기초자료와 분출자료를 비교하여 자동으로 변동을 탐지해 변동코드를 입력해 주고, 다양한 국토지리원 배포 지도자료를 중첩할 수 있도록 편리하게 불러오고, 다양한 국토지리정보원 배포 영상자료를 중첩해 봐서 자료간의 불일치를 찾는 것이 목적입니다.
또한 각 자료를 세트로 취급하여 투명도를 조절하고, 색을 일괄변경하고, 별도의 창으로 분리하는 기능과 다양한 인터넷나 원 내의 최신 국토기본정보 지도를 배경으로 깔 수 있는 기능도 있습니다.

## 사용자 지침서
상세한 사용자 지침서는 아래의 링크에서 보실 수 있습니다.

[사용자 지침서](docs/manual/manual.md)

## 설치 지침서
아직 설치를 안 하신 분은 설치 지침서를 통해 QGIS 설치부터 국토지리정보원 QGIS  플러그인 저장소 설정, 플러그인 설정 등의 방법을 익히실 수 있습니다.

[설치 지침서](docs/install/install.md)

## 버그신고
사용중 버그를 발견하시면 다음의 링크를 통해서 알려주세요. '한글로' 기록해 주시면 됩니다.
최선을 다해 수정방법을 찾아보겠습니다.

[버그신고](https://github.com/kr-ngii/NgiiDataOverlay/issues/new?template=bug_report.md)

## 개선요청
쓰시다가 이렇게 하면 더 쉽게 작업을 할 수 있지 않을까 하는 것이 떠오르시면 아래의 링크를 통해 알려주세요.

[개선요청](https://github.com/kr-ngii/NgiiDataOverlay/issues/new?template=feature_request.md)

## 기타 문의사항
쓰시다가 버그도 아니고 개선요청도 아니지만 궁금한 것이 있으면 물어봐 주세요.

[문의사항](https://github.com/kr-ngii/NgiiDataOverlay/issues/new?template=question.md)

## 라이선스
 * 이 프로그램은 오픈소스 표준 라이선스인 [GPL2](LICENSE)를 따릅니다.
 * 이 프로그램에는 다음 QGIS 플러그인 및 파이썬 라이브러리가 포함되어 있습니다.
   - Dockable MirrorMap plugin: <https://plugins.qgis.org/plugins/DockableMirrorMap/>
   - OpenLayers plugin: <https://plugins.qgis.org/plugins/openlayers_plugin/>
   - TMS for Korea plugin: <https://plugins.qgis.org/plugins/tmsforkorea/>
   - PyPDF2 package: <https://pythonhosted.org/PyPDF2/>
   - dbfread package: <https://dbfread.readthedocs.io>
