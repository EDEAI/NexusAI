import { Spin } from "antd";

/*
 * @LastEditors: biz
 */
export default function Loading() {
    return (
        <div className="w-screen h-screen flex justify-center items-center">
            <Spin size="large" />
        </div>
    );
}
